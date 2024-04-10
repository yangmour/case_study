package com.xiwen.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.cloud.context.config.annotation.RefreshScope;

/**
 * Swagger配置属性
 *
 * @since 2021-04-05
 */
@RefreshScope
@ConfigurationProperties(prefix = "netrain.swagger")
public class SwaggerProperties {

    /**
     * 是否启用Swagger
     */
    private boolean enable;

    /**
     * 扫描的基本包
     */
    private String basePackage;

    /**
     * ApiInfo标题
     */
    private String title;

    /**
     * ApiInfo描述
     */
    private String description;

    /**
     * ApiInfo版权信息
     */
    private String license;

    /**
     * ApiInfo协议地址
     */
    private String serviceUrl;

    /**
     * 联系人姓名
     */
    private String contactName;

    /**
     * 联系人URL
     */
    private String contactUrl;

    /**
     * 联系人邮箱
     */
    private String contactEmail;

    public boolean isEnable() {
        return enable;
    }

    public void setEnable(boolean enable) {
        this.enable = enable;
    }

    public String getBasePackage() {
        return basePackage;
    }

    public void setBasePackage(String basePackage) {
        this.basePackage = basePackage;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getLicense() {
        return license;
    }

    public void setLicense(String license) {
        this.license = license;
    }

    public String getServiceUrl() {
        return serviceUrl;
    }

    public void setServiceUrl(String serviceUrl) {
        this.serviceUrl = serviceUrl;
    }

    public String getContactName() {
        return contactName;
    }

    public void setContactName(String contactName) {
        this.contactName = contactName;
    }

    public String getContactUrl() {
        return contactUrl;
    }

    public void setContactUrl(String contactUrl) {
        this.contactUrl = contactUrl;
    }

    public String getContactEmail() {
        return contactEmail;
    }

    public void setContactEmail(String contactEmail) {
        this.contactEmail = contactEmail;
    }

    @Override
    public String toString() {
        return "SwaggerProperties{" +
                "enable=" + enable +
                ", basePackage='" + basePackage + '\'' +
                ", title='" + title + '\'' +
                ", description='" + description + '\'' +
                ", license='" + license + '\'' +
                ", serviceUrl='" + serviceUrl + '\'' +
                ", contactName='" + contactName + '\'' +
                ", contactUrl='" + contactUrl + '\'' +
                ", contactEmail='" + contactEmail + '\'' +
                '}';
    }
}
