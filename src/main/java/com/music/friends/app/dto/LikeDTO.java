package com.music.friends.app.dto;

import lombok.Data;

@Data
public class LikeDTO {

    private String id;

    private String likeId;

    private String userId;

    private String createTime;

    private Integer type;

    private String likedUserId;
}
