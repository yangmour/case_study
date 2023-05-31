package com.atguigu.syt.cmn.service;


import com.atguigu.syt.model.cmn.Region;
import com.atguigu.syt.vo.cmn.RegionVo;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;

/**
 * <p>
 *  服务类
 * </p>
 *
 * @author xiwen
 * @since 2023-05-31
 */
public interface RegionService extends IService<Region> {

    List<RegionVo> getByParentCode(String parentCode);
}
