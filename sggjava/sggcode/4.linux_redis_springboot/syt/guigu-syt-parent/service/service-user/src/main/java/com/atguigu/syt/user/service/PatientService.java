package com.atguigu.syt.user.service;


import com.atguigu.syt.model.user.Patient;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;

/**
 * <p>
 * 就诊人表 服务类
 * </p>
 *
 * @author xiwen
 * @since 2023-06-07
 */
public interface PatientService extends IService<Patient> {

    boolean deleteByPidAndUid(Long userId, Long pid);

    Patient getByUidAndPid(Long userId, Long pid);

    List<Patient> findAll(Long userId);
}
