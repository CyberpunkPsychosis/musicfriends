package com.music.friends.app.dto;

import lombok.Data;

@Data
public class MusicDTO {

    private String id;

    private String url;

    private String userId;

    private String createTime;

    private String name;

    private String introduce;

    private Integer pageNum;

    private Integer pageSize;
}
