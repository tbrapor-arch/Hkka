# Downloads reference material for writing the Hakka course: the MOE 客語知識庫 articles on grammar, vocabulary,
# pronunciation and the Sixian/Hailu overviews (hakkadict.moe.edu.tw/resource/), the MOE romanisation manual and
# workbooks, and the Hakka Council 語料選粹 graded texts. Copyrighted (MOE / 客委會): for the PRIVATE repo only.
# Run in PowerShell, in the folder that holds this file:
#   powershell -ExecutionPolicy Bypass -File .\fetch_references.ps1
# It makes hakka-references.zip next to the folder: send that file to Claude.
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$out = Join-Path (Get-Location) "hakka-references"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$files = @(
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/114_012_%E8%87%BA%E7%81%A3%E5%AE%A2%E8%AA%9E%E7%AC%AC%E4%B8%80%E4%BA%BA%E7%A8%B1%E6%89%80%E6%9C%89%E6%A0%BC.pdf", "語法_114_012_臺灣客語第一人稱所有格.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/112_033_%E5%AE%A2%E8%AA%9E%E7%9A%84%E7%9B%AE%E7%9A%84%E5%8F%A5%E5%BC%8F.pdf", "語法_112_033_客語的目的句式.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/112_032_%E5%AE%A2%E8%AA%9E%E7%9A%84%E3%80%8C%E4%BE%86%E5%8E%BB%E3%80%8D%E5%8F%A5%E5%BC%8F%EF%BC%88%E4%B8%8B%EF%BC%89.pdf", "語法_112_032_客語的「來去」句式(下).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/112_031_%E5%AE%A2%E8%AA%9E%E7%9A%84%E3%80%8C%E4%BE%86%E5%8E%BB%E3%80%8D%E5%8F%A5%E5%BC%8F%EF%BC%88%E4%B8%8A%EF%BC%89.pdf", "語法_112_031_客語的「來去」句式(上).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/112_030_%E5%AE%A2%E8%AA%9E%E7%9A%84%E3%80%8C%E6%9C%83%E3%80%8D%EF%BC%88%E4%B8%8B%EF%BC%89.pdf", "語法_112_030_客語的「會」(下).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/112_029_%E5%AE%A2%E8%AA%9E%E7%9A%84%E3%80%8C%E6%9C%83%E3%80%8D%EF%BC%88%E4%B8%8A%EF%BC%89.pdf", "語法_112_029_客語的「會」(上).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/111_025_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E7%B5%A6%E4%BA%88%E5%8F%A5%E5%BC%8F.pdf", "語法_111_025_客家語的給予句式.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/111_024_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E3%80%8C%E9%81%8E%E3%80%8D.pdf", "語法_111_024_客家語的「過」.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/111_023_%E8%87%BA%E7%81%A3%E5%AE%A2%E5%AE%B6%E8%AA%9E%E3%80%8C%E6%81%81%E3%80%8D%E7%9A%84%E8%AA%9E%E7%94%A8%E8%AE%8A%E8%AA%BF.pdf", "語法_111_023_臺灣客家語「恁」的語用變調.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/111_022_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E3%80%8C%E6%81%81%E3%80%8D%E6%A7%8B%E5%BC%8F%E7%9A%84%E7%BF%92%E8%AA%9E%E5%8C%96%EF%BC%88%E4%B8%8B%EF%BC%89.pdf", "語法_111_022_客家語「恁」構式的習語化(下).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/111_021_%E8%87%BA%E7%81%A3%E5%AE%A2%E5%AE%B6%E8%AA%9E%E3%80%8C%E6%81%81%E3%80%8D%E6%A7%8B%E5%BC%8F%E7%9A%84%E7%BF%92%E8%AA%9E%E5%8C%96%EF%BC%88%E4%B8%8A%EF%BC%89.pdf", "語法_111_021_臺灣客家語「恁」構式的習語化(上).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/111_020_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E3%80%8C%E6%AD%A3%E3%80%8D.pdf", "語法_111_020_客家語的「正」.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/111_019_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E3%80%8C%E5%A5%BD%E3%80%8D%E7%9A%84%E5%A4%9A%E7%BE%A9%E6%80%A7%EF%BC%88%E4%B8%8B%EF%BC%89.pdf", "語法_111_019_客家語「好」的多義性(下).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/111_018_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E3%80%8C%E5%A5%BD%E3%80%8D%E7%9A%84%E5%A4%9A%E7%BE%A9%E6%80%A7%EF%BC%88%E4%B8%8A%EF%BC%89.pdf", "語法_111_018_客家語「好」的多義性(上).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/110_%E8%A9%9E%E5%88%86_024_%E5%AE%A2%E8%AA%9E%E3%80%8C%E7%B7%8AX%E7%B7%8A%EF%BC%B9%E3%80%8D%E5%8F%A5%E5%BC%8F.pdf", "語法_110_詞分_024_客語「緊X緊Ｙ」句式.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/110_037_%E5%9B%9B%E7%B8%A3%E5%AE%A2%E8%AA%9E%E7%9F%AD%E6%99%82%E8%B2%8C%E6%A8%99%E8%A8%98%E3%80%8C%E5%95%8A%E3%80%8D%E7%9A%84%E5%B9%BE%E5%80%8B%E7%94%A8%E6%B3%95.pdf", "語法_110_037_四縣客語短時貌標記「啊」的幾個用法.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/110_036_%E5%9B%9B%E7%B8%A3%E5%AE%A2%E8%AA%9E%E5%90%88%E9%9F%B3%E8%A9%9E%E3%80%8C%E6%AF%8B%E4%BF%82%EF%BC%88me55%EF%BC%89%E3%80%8D%E7%9A%84%E5%B9%BE%E7%A8%AE%E7%94%A8%E6%B3%95.pdf", "語法_110_036_四縣客語合音詞「毋係(me55)」的幾種用法.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/110_035_%E5%9B%9B%E7%B8%A3%E5%AE%A2%E8%AA%9E%E3%80%8CV%E5%8B%95%E8%A9%9E%2B%E7%AD%89%2B%E4%BE%86%E3%80%8D%E5%8F%A5%E5%BC%8F%E7%9A%84%E9%A1%9E%E5%9E%8B.pdf", "語法_110_035_四縣客語「V動詞+等+來」句式的類型.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/109_035_%E5%AE%A2%E8%AA%9E%E7%9A%84%E6%AF%94%E8%BC%83%E5%8F%A5.pdf", "語法_109_035_客語的比較句.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/109_034_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E8%A4%87%E5%8F%A5%EF%BC%88%E4%B8%8B%EF%BC%89.pdf", "語法_109_034_客家語的複句(下).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/109_033_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E8%A4%87%E5%8F%A5%EF%BC%88%E4%B8%8A%EF%BC%89.pdf", "語法_109_033_客家語的複句(上).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/109_032_%E5%AE%A2%E5%AE%B6%E8%A9%B1%E7%9A%84%E6%A7%8B%E8%A9%9E%E2%80%94%E5%89%8D%E7%B6%B4%E3%80%81%E4%B8%AD%E7%B6%B4%E8%88%87%E5%BE%8C%E7%B6%B4.pdf", "語法_109_032_客家話的構詞—前綴、中綴與後綴.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/109_031_%E5%AE%A2%E5%AE%B6%E8%A9%B1%E7%9A%84%E5%BD%A2%E5%AE%B9%E8%A9%9E%E9%87%8D%E7%96%8A%E5%BC%8F.pdf", "語法_109_031_客家話的形容詞重疊式.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/109_030_%E5%AE%A2%E8%AA%9E%E7%9A%84%E8%AA%9E%E5%BA%8F%28%E4%BA%8C%29.pdf", "語法_109_030_客語的語序(二).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/109_029_%E5%AE%A2%E8%AA%9E%E7%9A%84%E8%AA%9E%E5%BA%8F%28%E4%B8%80%29.pdf", "語法_109_029_客語的語序(一).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/109_028_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E9%9B%99%E8%B3%93%E5%8F%A5.pdf", "語法_109_028_客家語的雙賓句.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/109_027_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E6%99%82%E8%B2%8C%E5%8F%A5.pdf", "語法_109_027_客家語的時貌句.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/108_031_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E3%80%8C%E5%90%8C%E3%80%8D%E8%88%87%E3%80%8C%E6%91%8E%E3%80%8D%E7%9A%84%E8%AA%9E%E6%B3%95%E5%8A%9F%E8%83%BD.pdf", "語法_108_031_客家語「同」與「摎」的語法功能.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/108_030_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E3%80%8C%E5%88%86%E3%80%8D%E7%9A%84%E8%AA%9E%E6%B3%95%E5%8A%9F%E8%83%BD.pdf", "語法_108_030_客家語「分」的語法功能.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/108_029_%E5%AE%A2%E5%AE%B6%E8%A9%B1%E7%9A%84%E3%80%8C%E6%9C%89%E3%80%8D.pdf", "語法_108_029_客家話的「有」.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/108_028_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E5%B7%AE%E6%AF%94%E5%8F%A5%E9%A1%9E%E5%9E%8B.pdf", "語法_108_028_客家語的差比句類型.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/108_027_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E8%AA%9E%E6%B3%95%E7%9A%84%E5%85%A7%E9%83%A8%E5%B7%AE%E7%95%B0%EF%BC%88%E4%B8%8B%EF%BC%89.pdf", "語法_108_027_客家語語法的內部差異(下).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/108_026_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E8%AA%9E%E6%B3%95%E7%9A%84%E5%85%A7%E9%83%A8%E5%B7%AE%E7%95%B0%EF%BC%88%E4%B8%8A%EF%BC%89.pdf", "語法_108_026_客家語語法的內部差異(上).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/107_020_%E5%AE%A2%E8%AA%9E%E7%9A%84%E9%87%8D%E7%96%8A%E6%A7%8B%E8%A9%9E.pdf", "語法_107_020_客語的重疊構詞.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E6%B3%95/107_019_%E5%AE%A2%E8%AA%9E%E7%9A%84%E7%9B%B8%E5%8F%8D%E8%A9%9E%E5%BA%8F.pdf", "語法_107_019_客語的相反詞序.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/114_006_%E8%87%BA%E7%81%A3%E5%AE%A2%E5%AE%B6%E7%9A%84%E5%8E%9F%E8%89%B2%E8%A9%9E.pdf", "詞彙_114_006_臺灣客家的原色詞.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/114_004_%E8%87%BA%E7%81%A3%E6%B5%B7%E9%99%B8%E5%AE%A2%E8%AA%9E%E7%9A%84%E5%B0%8F%E7%A8%B1%E8%A9%9E%E8%88%87%E5%B0%8F%E7%A8%B1%E9%AB%98%E8%AA%BF%E5%BE%B5%E6%80%A7.pdf", "詞彙_114_004_臺灣海陸客語的小稱詞與小稱高調徵性.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/114_005_%E5%AE%A2%E8%AA%9E%E8%A3%A1%E4%BB%A5%E6%89%8B%E5%BA%A6%E9%87%8F%E7%9A%84%E9%87%8F%E8%A9%9E.pdf", "詞彙_114_005_客語裡以手度量的量詞.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/112_006_%E8%87%BA%E7%81%A3%E5%AE%A2%E8%AA%9E%E7%9A%84%E7%A8%8B%E5%BA%A6%E5%89%AF%E8%A9%9E.pdf", "詞彙_112_006_臺灣客語的程度副詞.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/112_005_%E8%87%BA%E7%81%A3%E5%AE%A2%E8%AA%9E%E7%9A%84%E3%80%8C%E4%BB%94%E5%B0%BE%E8%A9%9E%E3%80%8D%EF%BC%88%E4%B8%8B%EF%BC%89.pdf", "詞彙_112_005_臺灣客語的「仔尾詞」(下).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/112_004_%E8%87%BA%E7%81%A3%E5%AE%A2%E8%AA%9E%E7%9A%84%E3%80%8C%E4%BB%94%E5%B0%BE%E8%A9%9E%E3%80%8D%EF%BC%88%E4%B8%8A%EF%BC%89.pdf", "詞彙_112_004_臺灣客語的「仔尾詞」(上).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/111_030_%E8%87%BA%E7%81%A3%E5%AE%A2%E5%AE%B6%E8%AA%9E%E5%80%9F%E8%A9%9E%E7%9A%84%E7%AD%96%E7%95%A5%EF%BC%88%E4%B8%8B%EF%BC%89.pdf", "詞彙_111_030_臺灣客家語借詞的策略(下).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/111_029_%E8%87%BA%E7%81%A3%E5%AE%A2%E5%AE%B6%E8%AA%9E%E5%80%9F%E8%A9%9E%E7%9A%84%E7%AD%96%E7%95%A5%EF%BC%88%E4%B8%8A%EF%BC%89.pdf", "詞彙_111_029_臺灣客家語借詞的策略(上).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/111_027_%E8%87%BA%E7%81%A3%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E4%BA%BA%E7%A8%B1%E4%BB%A3%E5%90%8D%E8%A9%9E%EF%BC%88%E4%B8%8B%EF%BC%89.pdf", "詞彙_111_027_臺灣客家語的人稱代名詞(下).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/111_026_%E8%87%BA%E7%81%A3%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E4%BA%BA%E7%A8%B1%E4%BB%A3%E5%90%8D%E8%A9%9E%EF%BC%88%E4%B8%8A%EF%BC%89.pdf", "詞彙_111_026_臺灣客家語的人稱代名詞(上).pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/110_%E8%A9%9E%E5%88%86_023_%E5%AE%A2%E8%AA%9E%E7%9A%84%E5%90%A6%E5%AE%9A%E8%A9%9E.pdf", "詞彙_110_詞分_023_客語的否定詞.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/110_007_%E3%80%8C%E8%BD%89%E3%80%8D%E8%88%87%E3%80%8C%E6%AD%B8%E3%80%8D.pdf", "詞彙_110_007_「轉」與「歸」.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/107_018_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E8%A9%9E%E5%BD%99%E4%B8%AD%E7%9A%84%E9%96%A9%E5%8D%97%E8%AA%9E%E5%80%9F%E8%A9%9E.pdf", "詞彙_107_018_客家語詞彙中的閩南語借詞.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%A9%9E%E5%BD%99/107_017_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E7%89%B9%E5%BE%B5%E8%A9%9E.pdf", "詞彙_107_017_客家語的特徵詞.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E9%9F%B3/107_015_%E8%87%BA%E7%81%A3%E5%9B%9B%E7%B8%A3%E8%85%94%E3%80%81%E6%B5%B7%E9%99%B8%E8%85%94%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E9%80%A3%E8%AE%80%E8%AE%8A%E8%AA%BF.pdf", "語音_107_015_臺灣四縣腔、海陸腔客家語的連讀變調.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E9%9F%B3/107_014_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E6%96%87%E7%99%BD%E7%95%B0%E8%AE%80.pdf", "語音_107_014_客家語的文白異讀.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E9%9F%B3/107_013_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E8%AA%9E%E9%9F%B3%E7%89%B9%E8%89%B2.pdf", "語音_107_013_客家語的語音特色.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E8%AA%9E%E9%9F%B3/107_012_%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%9A%84%E9%9F%B3%E7%AF%80%E7%B5%90%E6%A7%8B.pdf", "語音_107_012_客家語的音節結構.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E7%B6%9C%E8%AB%96/107_004_%E8%87%BA%E7%81%A3%E6%B5%B7%E9%99%B8%E8%85%94%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%B0%A1%E4%BB%8B.pdf", "綜論_107_004_臺灣海陸腔客家語簡介.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E7%B6%9C%E8%AB%96/107_003_%E8%87%BA%E7%81%A3%E5%9B%9B%E7%B8%A3%E8%85%94%E5%AE%A2%E5%AE%B6%E8%AA%9E%E7%B0%A1%E4%BB%8B.pdf", "綜論_107_003_臺灣四縣腔客家語簡介.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E7%B6%9C%E8%AB%96/107_002_%E8%87%BA%E7%81%A3%E5%AE%A2%E5%AE%B6%E8%A9%B1%E7%9A%84%E5%88%86%E5%B8%83%E5%8F%8A%E4%BD%BF%E7%94%A8%E6%A6%82%E6%B3%81.pdf", "綜論_107_002_臺灣客家話的分布及使用概況.pdf"),
  @("https://hakkadict.moe.edu.tw/static/resource/%E5%AE%A2%E8%AA%9E%E8%B3%87%E6%BA%90%E4%B8%8B%E8%BC%89/%E5%85%B6%E4%BB%96%E8%B3%87%E6%BA%90/hakka_pinyin3.pdf", "拼音_客家語拼音方案使用手冊.pdf"),
  @("https://language.moe.gov.tw/files/people_files/%E5%AE%A2%E5%AE%B6%E8%AA%9E%E6%8B%BC%E9%9F%B3%E5%AD%B8%E7%BF%92%E6%89%8B%E5%86%8A_%E5%9B%9B%E7%B8%A3%E8%85%94.pdf", "拼音_客家語拼音學習手冊_四縣腔.pdf"),
  @("https://language.moe.gov.tw/files/people_files/%E5%AE%A2%E5%AE%B6%E8%AA%9E%E6%8B%BC%E9%9F%B3%E5%AD%B8%E7%BF%92%E6%89%8B%E5%86%8A_%E6%B5%B7%E9%99%B8%E8%85%94.pdf", "拼音_客家語拼音學習手冊_海陸腔.pdf"),
  @("https://elearning.hakka.gov.tw/hakka/files/downloads/245.zip", "語料選粹_四縣.zip"),
  @("https://elearning.hakka.gov.tw/hakka/files/downloads/246.zip", "語料選粹_海陸.zip")
)
$ok = 0; $fail = 0
foreach ($f in $files) {
  $dest = Join-Path $out $f[1]
  if ((Test-Path $dest) -and ((Get-Item $dest).Length -gt 0)) { Write-Host "have $($f[1])"; $ok++; continue }
  $part = "$dest.part"   # download to .part, rename when complete: an interrupted file is fetched again next run
  try {
    Invoke-WebRequest -UseBasicParsing -Uri $f[0] -OutFile $part
    Move-Item -Force $part $dest
    Write-Host "ok   $($f[1])"; $ok++
  } catch { Write-Host "FAIL $($f[1])" -ForegroundColor Red; $fail++; Remove-Item -ErrorAction SilentlyContinue $part }
}
$zip = "$out.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path "$out\*" -DestinationPath $zip
Write-Host ""
Write-Host "$ok files, $fail failed. Send this file to Claude: $zip" -ForegroundColor Green
