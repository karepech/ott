<?php
$portal   = "http://51.89.21.69:2052";
$username = "2585266034336160";
$password = "b4ba56207035";
$output_file = "maling.m3u";

$m3u_url = "{$portal}/get.php?username={$username}&password={$password}&type=m3u_plus&output=ts";

echo "Target URL: {$m3u_url}\n";

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $m3u_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_USERAGENT, 'OTT Navigator');
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 15);
curl_setopt($ch, CURLOPT_TIMEOUT, 120);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

$m3u_content = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($http_code == 200 && strpos($m3u_content, '#EXTM3U') !== false) {
    file_put_contents($output_file, $m3u_content);
    echo "SUKSES! File {$output_file} berhasil dibuat.\n";
} else {
    echo "GAGAL: HTTP Code {$http_code}\n";
}
?>
