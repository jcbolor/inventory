<?php

/**
 * Custom branding helper (RAKS Invoicing).
 *
 * Mirrors an uploaded company logo onto the Flutter login screen assets so the
 * pre-authentication login page shows the same logo as the admin area.
 *
 * The login screen exists in two front-ends, each with its own static assets:
 *   React portal (current login):
 *     public/invoiceninja-logo@light-*.png  (light background)
 *     public/invoiceninja-logo@dark-*.png   (dark background)
 *   Flutter portal:
 *     public/assets/assets/images/logo_light.png  (light background)
 *     public/assets/assets/images/logo_dark.png   (dark background)
 *
 * Two visual variants are produced:
 *   - the original uploaded logo (dark ink), shown on LIGHT backgrounds;
 *   - a white recolour (near-black pixels -> white), shown on DARK backgrounds.
 *
 * Note the naming conventions differ between front-ends:
 *   React  : invoiceninja-logo@dark  = dark-ink logo (the login uses this),
 *            invoiceninja-logo@light = white logo.
 *   Flutter: logo_light = dark-ink (light theme), logo_dark = white (dark theme).
 * So targets are grouped by INK colour, not by filename, to keep both correct.
 * Globs are used for the React assets so the sync survives bundle re-hashing.
 */

namespace App\Services\Logo;

class LoginLogoSync
{
    /** Targets (relative to public/) that receive the original dark-ink logo. */
    private const DARK_INK_TARGETS = [
        'invoiceninja-logo@dark-*.png',
        'assets/assets/images/logo_light.png',
    ];

    /** Targets (relative to public/) that receive the white recoloured logo. */
    private const WHITE_TARGETS = [
        'invoiceninja-logo@light-*.png',
        'assets/assets/images/logo_dark.png',
    ];

    /** Pixels darker than this luminance become white in the dark variant. */
    private const DARK_THRESHOLD = 60;

    /**
     * @param string $binary Raw image bytes of the uploaded logo.
     */
    public static function fromBinary(string $binary): void
    {
        try {
            if ($binary === '' || ! \function_exists('imagecreatefromstring')) {
                return;
            }

            $im = @imagecreatefromstring($binary);
            if ($im === false) {
                return;
            }

            imagealphablending($im, false);
            imagesavealpha($im, true);

            self::writeDarkInk($im);
            self::writeWhite($im);

            imagedestroy($im);
        } catch (\Throwable $e) {
            // Never let branding break the upload flow.
            nlog('LoginLogoSync failed: ' . $e->getMessage());
        }
    }

    /**
     * Resolve glob patterns (relative to public/) to concrete writable paths.
     *
     * @param  array<int,string> $patterns
     * @return array<int,string>
     */
    private static function resolveTargets(array $patterns): array
    {
        $paths = [];

        foreach ($patterns as $pattern) {
            $matches = glob(public_path($pattern)) ?: [];
            foreach ($matches as $match) {
                $paths[] = $match;
            }
        }

        return $paths;
    }

    private static function writable(string $target): bool
    {
        return is_writable($target) || is_writable(\dirname($target));
    }

    private static function writeDarkInk($im): void
    {
        foreach (self::resolveTargets(self::DARK_INK_TARGETS) as $target) {
            if (self::writable($target)) {
                imagepng($im, $target);
            }
        }
    }

    private static function writeWhite($im): void
    {
        $targets = array_filter(self::resolveTargets(self::WHITE_TARGETS), [self::class, 'writable']);

        if ($targets === []) {
            return;
        }

        $w = imagesx($im);
        $h = imagesy($im);

        $out = imagecreatetruecolor($w, $h);
        imagealphablending($out, false);
        imagesavealpha($out, true);
        imagefilledrectangle($out, 0, 0, $w, $h, imagecolorallocatealpha($out, 0, 0, 0, 127));

        for ($y = 0; $y < $h; $y++) {
            for ($x = 0; $x < $w; $x++) {
                $rgba = imagecolorat($im, $x, $y);

                $a = ($rgba >> 24) & 0x7F;
                $r = ($rgba >> 16) & 0xFF;
                $g = ($rgba >> 8) & 0xFF;
                $b = $rgba & 0xFF;

                $luminance = (0.299 * $r) + (0.587 * $g) + (0.114 * $b);

                if ($luminance < self::DARK_THRESHOLD) {
                    $r = $g = $b = 255;
                }

                imagesetpixel($out, $x, $y, imagecolorallocatealpha($out, $r, $g, $b, $a));
            }
        }

        foreach ($targets as $target) {
            imagepng($out, $target);
        }

        imagedestroy($out);
    }
}
