package com.music.friends.app.service;

import com.music.friends.app.pojo.Idea;

import java.util.List;
import java.util.Map;

/**
 * 动态Service
 */
public interface IdeaService {

    /**
     * 根据主键删除动态
     * @param id 主键
     * @return Boolean
     */
    Boolean deleteByPrimaryKey(String id);

    /**
     * 插入动态
     * @param idea 实体
     * @return Boolean
     */
    Boolean insert(Idea idea);

    /**
     * 根据用户主键查询动态
     * @param userId 用户主键
     * @return List<Idea>
     */
    List<Idea> selectByUserId(String userId);

    /**
     * 查询所有公开动态
     * @return List<Idea>
     */
    Map<String, Object> selectAllPublicFriendsMyself(String userId, Integer pageNum, Integer pageSize);

    Idea selectById(String id);
}
