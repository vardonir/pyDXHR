from pyDXHR.utils import crc32bzip2
from pyDXHR.cdcEngine.Archive import Archive, ArchiveEntry

pc_dc_path = r"F:\Games\Deus Ex HRDC\BIGFILE.000"
pc_arc = Archive()
pc_arc.deserialize_from_file(pc_dc_path)

arc_entry = pc_arc.get_from_hash(0x119CE2CA, spec=0xFFFFFFFF, as_bytes=False)

pc_arc.Entries = []

xml_data = b'<dx3>\r\n  <Version>2.0.779</Version>\r\n  <Content>160928</Content>\r\n  <patches>\r\n    <Item Name="isPatch" Value="0"/>\r\n    <Item Name="patchCode" Value=""/>\r\n    <Item Name="patchContent" Value=""/>\r\n  </patches>\r\n  <switches>\r\n    <Item Name="buildCode" Value="1"/>\r\n    <Item Name="buildContent" Value="1"/>\r\n    <Item Name="cleanBuildCode" Value="1"/>\r\n    <Item Name="depFileParser" Value="0"/>\r\n    <Item Name="deploySymbols" Value="1"/>\r\n    <Item Name="buildLocalized" Value="1"/>\r\n    <Item Name="analyzeResources" Value="0"/>\r\n    <Item Name="createPs3Iso" Value="1"/>\r\n    <Item Name="createBigFile" Value="1"/>\r\n    <Item Name="deployQA" Value="0"/>\r\n    <Item Name="deployDev" Value="0"/>\r\n    <Item Name="triggerDemo" Value="0"/>\r\n    <Item Name="applyCheckpoint" Value="0"/>\r\n  </switches>\r\n</dx3>\r\n'
arc_entry.EntryData = xml_data
arc_entry.UncompressedSize = len(xml_data)

pc_arc.append(arc_entry)

new_bigfile = pc_arc.serialize()

from pathlib import Path

for idx, byte_data in enumerate(new_bigfile):
    output_file = fr"F:\Projects\pyDXHR\output\drm_test\xml.00{idx}"

    print(f"Writing to {Path(output_file).name}")
    with open(output_file, "wb") as f:
        f.write(byte_data)

print("Final checks")
new_arc = Archive()
new_arc.deserialize_from_file(fr"F:\Projects\pyDXHR\output\drm_test\xml.000")

breakpoint()
