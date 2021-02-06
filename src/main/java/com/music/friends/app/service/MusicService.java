package com.music.friends.app.service;

import com.music.friends.app.pojo.Music;

import java.util.List;
import java.util.Map;

public interface MusicService {

    Boolean insert(Music music);

    Boolean delete(String id);

    Boolean update(Music music);

    Music selectById(String id);

    List<Music> selectAll();

    Map<String, Object> listForPage(Music music, Integer pageNum, Integer pageSize);
}
