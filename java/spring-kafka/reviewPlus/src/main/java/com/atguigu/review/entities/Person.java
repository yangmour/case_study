package com.atguigu.review.entities;


import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
public class Person
{
    private Integer id;
    private String  personName;

    public Person(String personName)
    {
        this.personName = personName;
    }
}
