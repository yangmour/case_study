package org.example;

import com.itextpdf.text.*;
import com.itextpdf.text.pdf.*;

import java.io.FileOutputStream;
import java.io.IOException;

public class PdfPTableExample {

    public static void main(String[] args) throws IOException, DocumentException {
        Document document = new Document();
        PdfWriter.getInstance(document, new FileOutputStream("TableWithChineseAndImage.pdf"));

        document.open();

        // 添加中文字体
        BaseFont baseFont = BaseFont.createFont("STSongStd-Light", "UniGB-UCS2-H", BaseFont.NOT_EMBEDDED);
        Font font = new Font(baseFont, 10, Font.NORMAL, BaseColor.BLACK);

        // 创建一个包含3列的表格
        PdfPTable table = new PdfPTable(3);

        // 创建第一行（标题）
        PdfPCell cell1 = new PdfPCell(new Phrase("序号", font));
        PdfPCell cell2 = new PdfPCell(new Phrase("姓名", font));
        PdfPCell cell3 = new PdfPCell(new Phrase("照片", font));

        cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
        cell2.setHorizontalAlignment(Element.ALIGN_CENTER);
        cell3.setHorizontalAlignment(Element.ALIGN_CENTER);

        table.addCell(cell1);
        table.addCell(cell2);
        table.addCell(cell3);

        // 添加内容及图片
        Image image = Image.getInstance("/Users/xiwen/Desktop/dev/文档/imgs-test/WechatIMG7.jpg"); // 更改为实际图片路径
        image.scaleToFit(50, 50); // 设置图片大小

        for (int i = 1; i <= 5; i++) {
            table.addCell(new Phrase(String.valueOf(i), font)); // 序号
            table.addCell(new Phrase("张三" + i, font)); // 名字

            // 添加图片到表格
            PdfPCell imageCell = new PdfPCell(image, true);
            imageCell.setHorizontalAlignment(Element.ALIGN_CENTER);
            imageCell.setVerticalAlignment(Element.ALIGN_MIDDLE);
            table.addCell(imageCell);
        }

        // 加入表格
        document.add(table);

        document.close();
    }
}