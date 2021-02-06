package com.music.friends.app.pojo;

import java.util.Date;

/**
 *
 * This class was generated by MyBatis Generator.
 * This class corresponds to the database table music_friends_music
 *
 * @mbg.generated do_not_delete_during_merge
 */
public class Music {
    /**
     * Database Column Remarks:
     *   歌曲主键
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column music_friends_music.id
     *
     * @mbg.generated
     */
    private String id;

    /**
     * Database Column Remarks:
     *   歌曲存放地址
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column music_friends_music.url
     *
     * @mbg.generated
     */
    private String url;

    /**
     * Database Column Remarks:
     *   用户Id
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column music_friends_music.user_id
     *
     * @mbg.generated
     */
    private String userId;

    /**
     * Database Column Remarks:
     *   创建时间
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column music_friends_music.create_time
     *
     * @mbg.generated
     */
    private Date createTime;

    /**
     * Database Column Remarks:
     *   歌曲名称
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column music_friends_music.name
     *
     * @mbg.generated
     */
    private String name;

    /**
     * Database Column Remarks:
     *   歌曲简介
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column music_friends_music.introduce
     *
     * @mbg.generated
     */
    private String introduce;

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column music_friends_music.id
     *
     * @return the value of music_friends_music.id
     *
     * @mbg.generated
     */
    public String getId() {
        return id;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column music_friends_music.id
     *
     * @param id the value for music_friends_music.id
     *
     * @mbg.generated
     */
    public void setId(String id) {
        this.id = id == null ? null : id.trim();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column music_friends_music.url
     *
     * @return the value of music_friends_music.url
     *
     * @mbg.generated
     */
    public String getUrl() {
        return url;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column music_friends_music.url
     *
     * @param url the value for music_friends_music.url
     *
     * @mbg.generated
     */
    public void setUrl(String url) {
        this.url = url == null ? null : url.trim();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column music_friends_music.user_id
     *
     * @return the value of music_friends_music.user_id
     *
     * @mbg.generated
     */
    public String getUserId() {
        return userId;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column music_friends_music.user_id
     *
     * @param userId the value for music_friends_music.user_id
     *
     * @mbg.generated
     */
    public void setUserId(String userId) {
        this.userId = userId == null ? null : userId.trim();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column music_friends_music.create_time
     *
     * @return the value of music_friends_music.create_time
     *
     * @mbg.generated
     */
    public Date getCreateTime() {
        return createTime;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column music_friends_music.create_time
     *
     * @param createTime the value for music_friends_music.create_time
     *
     * @mbg.generated
     */
    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column music_friends_music.name
     *
     * @return the value of music_friends_music.name
     *
     * @mbg.generated
     */
    public String getName() {
        return name;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column music_friends_music.name
     *
     * @param name the value for music_friends_music.name
     *
     * @mbg.generated
     */
    public void setName(String name) {
        this.name = name == null ? null : name.trim();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column music_friends_music.introduce
     *
     * @return the value of music_friends_music.introduce
     *
     * @mbg.generated
     */
    public String getIntroduce() {
        return introduce;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column music_friends_music.introduce
     *
     * @param introduce the value for music_friends_music.introduce
     *
     * @mbg.generated
     */
    public void setIntroduce(String introduce) {
        this.introduce = introduce == null ? null : introduce.trim();
    }
}