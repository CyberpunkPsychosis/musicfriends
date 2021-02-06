package com.music.friends.app.service;

import com.music.friends.app.pojo.Like;

public interface LikeService {

    Boolean insert(Like like);

    Integer count(String likeId);

    Boolean delete(String likeId, String userId);

    Integer count(String userId, String likedUserId);
}
