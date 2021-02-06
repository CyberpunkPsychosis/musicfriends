package com.music.friends.app.service;

import com.music.friends.app.pojo.Mv;

import java.util.Map;

public interface MvService {

    Boolean insert(Mv mv);

    Boolean delete(String id);

    Mv selectById(String id);

    Map<String, Object> listForPage(Mv mv, Integer pageNum, Integer pageSize);
}
