# OCR de Windows (Windows.Media.Ocr) sobre imágenes PNG. Escribe un JSON por imagen con renglones,
# palabras y cajas. Uso: powershell -File winocr.ps1 -InDir <carpeta> -Lang es-MX
param([string]$InDir, [string]$Lang = "es-MX")

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
        $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
        $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]

function Await($op, [Type]$type) {
    $m = $asTaskGeneric.MakeGenericMethod($type)
    $task = $m.Invoke($null, @($op))
    $task.Wait(-1) | Out-Null
    return $task.Result
}

$language = [Windows.Globalization.Language]::new($Lang)
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($language)
if ($null -eq $engine) { throw "No hay motor OCR para $Lang" }

Get-ChildItem -Path $InDir -Filter *.png | Sort-Object Name | ForEach-Object {
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($_.FullName)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
    $lines = @()
    foreach ($line in $result.Lines) {
        $words = @()
        foreach ($w in $line.Words) {
            $r = $w.BoundingRect
            $words += [ordered]@{ t = $w.Text; x = [math]::Round($r.X, 1); y = [math]::Round($r.Y, 1);
                w = [math]::Round($r.Width, 1); h = [math]::Round($r.Height, 1) }
        }
        $lines += [ordered]@{ text = $line.Text; words = $words }
    }
    $out = [ordered]@{ image = $_.Name; width = $bitmap.PixelWidth; height = $bitmap.PixelHeight; lines = $lines }
    $json = $out | ConvertTo-Json -Depth 6 -Compress
    [System.IO.File]::WriteAllText(($_.FullName -replace '\.png$', '.json'), $json, [System.Text.Encoding]::UTF8)
    $stream.Dispose()
}
