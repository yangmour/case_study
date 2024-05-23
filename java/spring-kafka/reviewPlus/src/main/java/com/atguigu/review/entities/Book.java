package com.atguigu.review.entities;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

/**
 * @auther zzyy
 * @create 2019-06-27 16:28
 */
@AllArgsConstructor
@NoArgsConstructor
@Data
@Accessors(chain = true)
public class Book
{
    private Integer id;
    private String  bookName;
    private double price;

    public static void main(String[] args)
    {
        Book book = new Book();
        book.setId(11).setBookName("aja");


    }
}
