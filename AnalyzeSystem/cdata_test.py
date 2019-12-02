import xml.etree.ElementTree as etree
#~ import cElementTree as etree

def CDATA(text=None):
	element = etree.Element(CDATA)
	element.text = text
	return element

class ElementTreeCDATA(etree.ElementTree):
	def write(self, file, node, encoding, namespaces):
		if node.tag is CDATA:
			text = node.text.encode(encoding)
			file.write("\n<![CDATA[%s]]>\n" % text)
		else:
			etree.ElementTree.write(self, file, node, encoding, namespaces)

if __name__ == "__main__":
	import sys

	text = """
	<?xml version='1.0' encoding='utf-8'?>
	<text>
	This is just some sample text.
	</text>
	"""

	e = etree.Element("data")
	cdata = CDATA(text)
	e.append(cdata)
	et = ElementTreeCDATA(e)
	et.write(sys.stdout,cdata, "utf-8",None)