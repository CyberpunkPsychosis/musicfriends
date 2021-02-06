package com.music.friends.app.service.impl;

import com.music.friends.app.dao.AuthorityMapper;
import com.music.friends.app.pojo.Authority;
import com.music.friends.app.pojo.User;
import com.music.friends.app.service.AuthorityService;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;

/**
 * 权限实现类
 */
@Service
public class AuthorityServiceImpl implements AuthorityService {
    @Resource
    private AuthorityMapper authorityMapper;

    @Override
    public List<SimpleGrantedAuthority> selectByUserId(User user) {
        List<Authority> authorities = authorityMapper.selectByUserId(user.getId());
        List<SimpleGrantedAuthority> simpleGrantedAuthorities = new ArrayList<>();
        authorities.forEach(authority -> {
            SimpleGrantedAuthority simpleGrantedAuthority = new SimpleGrantedAuthority(authority.getName());
            simpleGrantedAuthorities.add(simpleGrantedAuthority);
        });
        return simpleGrantedAuthorities;
    }
}
