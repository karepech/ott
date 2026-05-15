<?php
$target_url = "https://freeiptv2026.sepak7042.workers.dev";
$output_file = "playlist.m3u";

// Kumpulan User-Agent untuk meniru perangkat Android/Smart TV
$user_agents = [
    "Dalvik/2.1.0 (Linux; U; Android 13; SM-S908B Build/TP1A.220624.014)",
    "ExoPlayerDemo/2.18.1 (Linux;Android 12) ExoPlayerLib/2.18.1",
    "TiviMate/4.7.0 (Linux; Android 11)"
];
$random_ua = $user_agents[array_rand($user_agents)];

$ch = curl_init();

$headers = [
    "User-Agent: " . $random_ua,
    "Accept: */*",
    "Accept-Language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control: no-cache",
    "Connection: keep-alive",
    "Referer: https://freeiptv2026.sepak7042.workers.dev/",
    "Origin: https://freeiptv2026.sepak7042.workers.dev"
];

curl_setopt_array($ch, [
    CURLOPT_URL => $target_url,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_MAXREDIRS => 5,
    CURLOPT_TIMEOUT => 60,
    CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
    CURLOPT_CUSTOMREQUEST => "GET",
    CURLOPT_HTTPHEADER => $headers,
    CURLOPT_SSL_VERIFYPEER => false,
    CURLOPT_SSL_VERIFYHOST => false,
    CURLOPT_ENCODING => "gzip, deflate, br",
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$err = curl_error($ch);

curl_close($ch);

if ($err) {
    die("Error cURL: " . $err . "\n");
}

if (strpos($response, '#EXTM3U') !== false) {
    if (file_put_contents($output_file, $response)) {
        echo "✅ Sukses! Playlist disimpan. Ukuran: " . strlen($response) . " bytes.\n";
    } else {
        die("❌ Gagal menulis file playlist.m3u.\n");
    }
} else {
    die("❌ Gagal: Respon bukan M3U atau IP diblokir.\n");
}
?>
