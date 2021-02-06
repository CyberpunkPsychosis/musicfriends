package com.music.friends.app.dao;

import com.music.friends.app.pojo.Music;

import java.util.List;

public interface MusicMapper {
    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_music
     *
     * @mbg.generated
     */
    int deleteByPrimaryKey(String id);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_music
     *
     * @mbg.generated
     */
    int insert(Music record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_music
     *
     * @mbg.generated
     */
    int insertSelective(Music record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_music
     *
     * @mbg.generated
     */
    Music selectByPrimaryKey(String id);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_music
     *
     * @mbg.generated
     */
    int updateByPrimaryKeySelective(Music record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_music
     *
     * @mbg.generated
     */
    int updateByPrimaryKeyWithBLOBs(Music record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_music
     *
     * @mbg.generated
     */
    int updateByPrimaryKey(Music record);

    List<Music> selectAll(Music music);
}