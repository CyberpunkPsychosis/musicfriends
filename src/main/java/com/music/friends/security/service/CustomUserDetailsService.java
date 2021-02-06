package com.music.friends.security.service;

import com.music.friends.app.dao.UserMapper;
import com.music.friends.app.service.AuthorityService;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.List;

@Service
public class CustomUserDetailsService implements UserDetailsService {
    @Resource
    private UserMapper userMapper;
    @Resource
    private AuthorityService authorityService;

    @Override
    public UserDetails loadUserByUsername(String s) throws UsernameNotFoundException {
        com.music.friends.app.pojo.User user = userMapper.selectByUserName(s);
        if (user == null){
            throw new UsernameNotFoundException(s);
        }
        List<SimpleGrantedAuthority> simpleGrantedAuthorities = authorityService.selectByUserId(user);
        return new User(user.getAccount(), user.getPassword(),
                user.getEnabled(), user.getAccountNonExpired(),
                user.getCredentialsNonExpired(), user.getAccountNonLocked(), simpleGrantedAuthorities);
    }
}
