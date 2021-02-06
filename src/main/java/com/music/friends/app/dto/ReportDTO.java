package com.music.friends.app.dto;

import lombok.Data;

@Data
public class ReportDTO {

    private String id;

    private String reportId;

    private String userId;

    private String createTime;

    private String reason;

    private Integer pageNum;

    private Integer pageSize;
}
