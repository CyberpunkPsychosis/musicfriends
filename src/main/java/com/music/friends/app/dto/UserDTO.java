package com.music.friends.app.dto;

import lombok.Data;

import java.util.Date;

@Data
public class UserDTO {

    private String id;

    private String account;

    private String password;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 更新时间
     */
    private Date updateTime;

    private Boolean accountNonExpired;

    private Boolean accountNonLocked;

    private Boolean credentialsNonExpired;

    private Boolean enabled;
}
