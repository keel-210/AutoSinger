# -*- coding: utf-8 -*-

import lxml.etree as ET

vsq4_URI = "{http://www.yamaha.co.jp/vocaloid/schema/vsq4/}"
base_path = r"C:\Users\KEEL\Documents\GitHub\AutoSinger\AnalyzeSystem\base_vsqx.vsqx"
test_path = r"C:\Users\KEEL\Documents\GitHub\AutoSinger\AnalyzeSystem\test_vsqx.vsqx"
vsq4_namespace = "http://www.yamaha.co.jp/vocaloid/schema/vsq4/"
vsq4_xsi = "http://www.w3.org/2001/XMLSchema-instance"

def write_vsq4(path, SE_list,pitch_List):
	ET.register_namespace("ns", vsq4_namespace)
	ET.register_namespace("xsi", vsq4_xsi)
	root = read_vsqx_root(base_path)
	vsP = extract_vsPart(root)
	for p in pitch_List:
		add_cc(vsP, p[0], "P", p[1])
	for se in SE_list:
		add_note(vsP, se[0] * 480, se[1] * 480, se[2], se[3])
	write_xml(root, path)
	
def test_write():
	ET.register_namespace("ns", vsq4_namespace)
	ET.register_namespace("xsi", vsq4_xsi)
	root = read_vsqx_root(base_path)
	vsP = extract_vsPart(root)
	add_cc(vsP, 360, "P", 24)
	add_note(vsP, 0, 960, "か", "k a")
	print(type(root))
	write_xml(root,test_path)

def write_xml(root, path):
	tree = ET.ElementTree(root)
	tree.write(path, encoding="UTF-8", xml_declaration=True, method="xml", pretty_print=True)

def read_vsqx_root(path):
	parser = ET.XMLParser(remove_blank_text=True)
	tree = ET.parse(path,parser)
	return tree.getroot()

def extract_vsPart(root):
	return root.find(vsq4_URI+"vsTrack").find(vsq4_URI+"vsPart")

def add_cc(vsPart, time, id, value):
	cc = ET.SubElement(vsPart, "cc")
	t = ET.SubElement(cc, "t")
	t.text = str(time)
	v = ET.SubElement(cc, "v")
	v.set("id", id)
	v.text = str(value)

def add_note(vsPart, time, length,yomi_kana,sound_element, accept=50, bendDep=8, bendLen=0, decay=50, fallPort=0, opening=127, risePort=0, vibLen=0, vibType=0):
	note = ET.SubElement(vsPart, "note")
	t = ET.SubElement(note, "t")
	dur = ET.SubElement(note, "dur")
	n = ET.SubElement(note, "n")
	v = ET.SubElement(note, "v")
	y = ET.SubElement(note, "y")
	p = ET.SubElement(note, "p")
	nStyle = ET.SubElement(note, "nStyle")
	nStyle_SubElement(nStyle, "accept", accept)
	nStyle_SubElement(nStyle,"bendDep",bendDep)
	nStyle_SubElement(nStyle,"bendLen",bendLen)
	nStyle_SubElement(nStyle,"decay",decay)
	nStyle_SubElement(nStyle,"fallPort",fallPort)
	nStyle_SubElement(nStyle,"opening",opening)
	nStyle_SubElement(nStyle,"risePort",risePort)
	nStyle_SubElement(nStyle,"vibLen",vibLen)
	nStyle_SubElement(nStyle, "vibType", vibType)
	t.text = str(time)
	dur.text = str(length)
	n.text = str(60)
	v.text = str(64)
	y.text = ET.CDATA(yomi_kana)
	p.text = ET.CDATA(sound_element)
	
def nStyle_SubElement(nStyle, id, value):
	v = ET.SubElement(nStyle, "v")
	v.set("id", id)
	v.text = str(value)

if __name__ == "__main__":
	test_write()