package com.music.friends.app.service;

import com.music.friends.app.pojo.Report;

import java.util.Map;

public interface ReportService {

    Boolean insert(Report report);

    Map<String, Object> listForPage(Report report, Integer pageNum, Integer pageSize);
}
