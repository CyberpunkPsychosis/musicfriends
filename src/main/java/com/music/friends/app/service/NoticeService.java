package com.music.friends.app.service;

import com.music.friends.app.pojo.Notice;

import java.util.Map;

public interface NoticeService {

    Boolean insert(Notice notice);

    Boolean delete(String id);

    Map<String, Object> listForPage(Notice notice, Integer pageNum, Integer pageSize);
}
