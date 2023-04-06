package com.xiwen.mbg.bean;

public class Employees {
    /**
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column employees.id
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    private Integer id;

    /**
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column employees.last_name
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    private String lastName;

    /**
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column employees.email
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    private String email;

    /**
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column employees.gender
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    private Integer gender;

    /**
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column employees.salary
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    private Double salary;

    /**
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column employees.dept_id
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    private Integer deptId;

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column employees.id
     *
     * @return the value of employees.id
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public Integer getId() {
        return id;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column employees.id
     *
     * @param id the value for employees.id
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public void setId(Integer id) {
        this.id = id;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column employees.last_name
     *
     * @return the value of employees.last_name
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public String getLastName() {
        return lastName;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column employees.last_name
     *
     * @param lastName the value for employees.last_name
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column employees.email
     *
     * @return the value of employees.email
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public String getEmail() {
        return email;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column employees.email
     *
     * @param email the value for employees.email
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public void setEmail(String email) {
        this.email = email;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column employees.gender
     *
     * @return the value of employees.gender
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public Integer getGender() {
        return gender;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column employees.gender
     *
     * @param gender the value for employees.gender
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public void setGender(Integer gender) {
        this.gender = gender;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column employees.salary
     *
     * @return the value of employees.salary
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public Double getSalary() {
        return salary;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column employees.salary
     *
     * @param salary the value for employees.salary
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public void setSalary(Double salary) {
        this.salary = salary;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column employees.dept_id
     *
     * @return the value of employees.dept_id
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public Integer getDeptId() {
        return deptId;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column employees.dept_id
     *
     * @param deptId the value for employees.dept_id
     *
     * @mbg.generated Thu Apr 06 11:51:52 CST 2023
     */
    public void setDeptId(Integer deptId) {
        this.deptId = deptId;
    }

    @Override
    public String toString() {
        return "Employees{" +
                "id=" + id +
                ", lastName='" + lastName + '\'' +
                ", email='" + email + '\'' +
                ", gender=" + gender +
                ", salary=" + salary +
                ", deptId=" + deptId +
                '}';
    }
}