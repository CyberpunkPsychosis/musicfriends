package com.music.friends.app.service;

import com.music.friends.app.pojo.Concern;

import java.util.Map;

public interface ConcernService {

    Boolean insert(Concern concern);

    Boolean delete(String me, String other);

    Concern selectById(String me, String other);

    Map<String, Object> listForPage(Concern concern, Integer pageNum, Integer pageSize);
}
