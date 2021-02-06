package com.music.friends.app.service.impl;

import cn.hutool.core.util.IdUtil;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import com.music.friends.app.dao.ReportMapper;
import com.music.friends.app.pojo.Report;
import com.music.friends.app.service.ReportService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ReportServiceImpl implements ReportService {

    @Resource
    private ReportMapper reportMapper;

    @Override
    public Boolean insert(Report report) {
        report.setId(IdUtil.simpleUUID());
        report.setCreateTime(new Date());
        return reportMapper.insertSelective(report) == 1;
    }

    @Override
    public Map<String, Object> listForPage(Report report, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Report> reports = reportMapper.selectAll(report);
        PageInfo<Report> pageInfo = new PageInfo<>(reports);
        Map<String, Object> map = new HashMap<>();
        map.put("list", pageInfo.getList());
        map.put("total", pageInfo.getTotal());
        return map;
    }
}
