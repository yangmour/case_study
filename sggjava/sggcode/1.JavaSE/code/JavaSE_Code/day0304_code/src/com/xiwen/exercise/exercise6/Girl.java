package com.xiwen.exercise.exercise6;

/**
 * Description:
 *
 * @author: yf
 * @Create: 2023/3/4-21:49
 * @Version: 1.0
 */
public class Girl {
    private String name;

    public Girl() {
    }

    public Girl(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return "Girl{" +
                "name='" + name + '\'' +
                '}';
    }
}
