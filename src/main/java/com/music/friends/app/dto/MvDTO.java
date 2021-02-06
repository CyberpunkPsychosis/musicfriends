package com.music.friends.app.dto;

import lombok.Data;

@Data
public class MvDTO {

    private String id;

    private String name;

    private String userId;

    private String createTime;

    private String url;

    private String introduce;

    private Integer pageNum;

    private Integer pageSize;
}
