package com.music.friends.app.dto;

import lombok.Data;

@Data
public class NoticeDTO {

    private String id;

    private String title;

    private String createTime;

    private String userId;

    private String content;

    private Integer pageNum;

    private Integer pageSize;
}
