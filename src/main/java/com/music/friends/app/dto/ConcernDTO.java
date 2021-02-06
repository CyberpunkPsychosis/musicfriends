package com.music.friends.app.dto;

import lombok.Data;

@Data
public class ConcernDTO {

    private String me;

    private String other;

    private String createTime;

    private Integer pageNum;

    private Integer pageSize;
}
