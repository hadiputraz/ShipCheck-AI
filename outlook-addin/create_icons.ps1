Add-Type -AssemblyName System.Drawing

$assetDir = "C:\xampp\htdocs\ShipCheck-AI\outlook-addin\assets"

function New-ShipCheckIcon {
    param(
        [int]$Size,
        [string]$Path
    )

    $bitmap = New-Object System.Drawing.Bitmap($Size, $Size)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)

    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.Clear([System.Drawing.Color]::FromArgb(194, 24, 91))

    $fontSize = [Math]::Max(8, [Math]::Floor($Size * 0.34))
    $font = New-Object System.Drawing.Font("Segoe UI", $fontSize, [System.Drawing.FontStyle]::Bold)
    $brush = [System.Drawing.Brushes]::White

    $text = "SC"
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center

    $rect = New-Object System.Drawing.RectangleF(0, 0, $Size, $Size)
    $graphics.DrawString($text, $font, $brush, $rect, $format)

    $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)

    $format.Dispose()
    $font.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
}

New-ShipCheckIcon 16  "$assetDir\icon-16.png"
New-ShipCheckIcon 32  "$assetDir\icon-32.png"
New-ShipCheckIcon 64  "$assetDir\icon-64.png"
New-ShipCheckIcon 80  "$assetDir\icon-80.png"
New-ShipCheckIcon 128 "$assetDir\icon-128.png"

Write-Host "ShipCheck AI icons created."
