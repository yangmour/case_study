package com.xiwen


import io.swagger.annotations.ApiModel
import io.swagger.annotations.ApiModelProperty

/**
 *
 * @Desc
 *
 * @Date 6/24/22
 *
 * @userName zhaosai
 */
@ApiModel(value = "文件信息")
class FileDTO {

    @ApiModelProperty(value = "文件名称")
    String fileName

    @ApiModelProperty(value = "文件地址")
    String fileUrl

    @ApiModelProperty(value = "文件唯一性编码")
    String uniqFileId


}
