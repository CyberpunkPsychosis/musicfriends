package com.music.friends.app.dto;

import lombok.Data;

import java.util.List;

@Data
public class IdeaDTO {

    private String id;

    private List<String> pictures;

    private String createTime;

    private Integer authorityFlag;

    private String userId;

    private String content;

    private Integer pageNum;

    private Integer pageSize;
}
