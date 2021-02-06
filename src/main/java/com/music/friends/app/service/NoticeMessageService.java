package com.music.friends.app.service;

import com.music.friends.app.pojo.NoticeMessage;

import java.util.List;
import java.util.Map;

public interface NoticeMessageService {

    Boolean batchInsert(List<NoticeMessage> list);

    Boolean delete(String id);

    Map<String, Object> listForPage(NoticeMessage noticeMessage, Integer pageNum, Integer pageSize);
}
