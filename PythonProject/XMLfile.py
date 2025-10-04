import xml.etree.ElementTree as ET


# Create the root element
root = ET.Element("movies")

# Create child elements
movie1 = ET.SubElement(root, "movie", id="1")
movie1_title = ET.SubElement(movie1, "title")
movie1_title.text = "Zona Zamfirova"
movie1_year=ET.SubElement(movie1,"year")
movie1_year.text="2002"
movie1_genre=ET.SubElement(movie1,"genre")
movie1_genre.text="comedy"

movie2 = ET.SubElement(root, "movie", id="2")
movie2_title = ET.SubElement(movie2, "title")
movie2_title.text = "The Shawshank Redemption"
movie2_year=ET.SubElement(movie2,"year")
movie2_year.text="1994"
movie2_genre=ET.SubElement(movie2,"genre")
movie2_genre.text="drama"

# Create the tree structure
tree = ET.ElementTree(root)

# Write the XML to a file
tree.write("movies.xml", encoding="utf-8", xml_declaration=True)

# If you want to print the XML as a string
xml_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
print(xml_str)
