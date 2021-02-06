package com.music.friends.app.service;

import com.music.friends.app.pojo.User;
import org.springframework.security.core.authority.SimpleGrantedAuthority;

import java.util.List;

/**
 * 权限Service
 */
public interface AuthorityService {
    List<SimpleGrantedAuthority> selectByUserId(User user);
}
