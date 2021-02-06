package com.music.friends.app.service;

import com.music.friends.app.pojo.UnConcern;

import java.util.List;
import java.util.Map;


public interface UnConcernService {

    Boolean insert(UnConcern unConcern);

    Boolean delete(String me, String other);

    Map<String, Object> listForPage(UnConcern unConcern, Integer pageNum, Integer pageSize);

    List<UnConcern> selectAllFans(String userId);
}
