package com.xiwen


import io.swagger.annotations.ApiModel
import io.swagger.annotations.ApiModelProperty
import lombok.Data

/**
 *
 * @Desc
 *
 * @Date 6/24/22
 *
 * @userName zhaosai
 */
@ApiModel(value = "文件信息返回")
@Data
class FileResponseDTO {

    @ApiModelProperty(value = "文件唯一性编码")
    String uniqFileId

    String result

    String message

}
