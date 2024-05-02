package com.github.msorkhpar.pageextextractor.extractor;

import com.github.msorkhpar.pageextextractor.utils.WikiPage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.*;

@Slf4j
@RequiredArgsConstructor
public class WikipediaPageExtractor {

    private final static String NAMESPACE_MAIN = "0";

    public static WikiPage extractTextString(Element xmlPage) {
        if (xmlPage.getElementsByTagName("redirect").getLength() != 0) {
            return null;
        }
        String nsValue = xmlPage.getElementsByTagName("ns").item(0).getTextContent();
        if (!nsValue.equals(NAMESPACE_MAIN)) {
            return null;
        }
        String title = xmlPage.getElementsByTagName("title").item(0).getTextContent().replace(" ", "_");
        String id = xmlPage.getElementsByTagName("id").item(0).getTextContent();
        NodeList revisionList = xmlPage.getElementsByTagName("revision");
        if (revisionList.getLength() > 0) {
            Node revision = revisionList.item(0);
            NodeList textList = ((Element) revision).getElementsByTagName("text");
            if (textList.getLength() > 0) {
                Node textNode = textList.item(0);
                return new WikiPage(Long.valueOf(id), title, textNode.getTextContent());
            }
        }
        return null;
    }

    public static Element createPage(String xmlData) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(new InputSource(new StringReader(xmlData)));
        return doc.getDocumentElement();
    }


}
