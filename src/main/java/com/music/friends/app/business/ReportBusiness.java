package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import com.music.friends.app.dto.ReportDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.Report;
import com.music.friends.app.pojo.User;
import com.music.friends.app.service.ReportService;
import com.music.friends.app.service.UserService;
import com.music.friends.app.utils.BeanListUtil;
import com.music.friends.app.utils.SpringSecurityUtil;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@Component
public class ReportBusiness {

    @Resource
    private ReportService reportService;
    @Resource
    private UserService userService;

    public Boolean insert(ReportDTO reportDTO) throws CustomException{
        if (reportDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = userService.selectByUserName(SpringSecurityUtil.getUserName());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        Report report = BeanUtil.toBean(reportDTO, Report.class);
        report.setUserId(user.getId());
        return reportService.insert(report);
    }

    public Map<String, Object> listForPage(ReportDTO reportDTO) throws CustomException{
        if (reportDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Report report = BeanUtil.toBean(reportDTO, Report.class);
        Map<String, Object> map = reportService.listForPage(report, reportDTO.getPageNum(), reportDTO.getPageSize());
        List<Report> list = (List<Report>) map.get("list");
        map.put("list", BeanListUtil.toBeanList(list, ReportDTO.class));
        return map;
    }
}
