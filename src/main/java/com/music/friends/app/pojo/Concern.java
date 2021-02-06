package com.music.friends.app.pojo;

import java.util.Date;

/**
 *
 * This class was generated by MyBatis Generator.
 * This class corresponds to the database table music_friends_concern
 *
 * @mbg.generated do_not_delete_during_merge
 */
public class Concern {
    /**
     * Database Column Remarks:
     *   关注者
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column music_friends_concern.me
     *
     * @mbg.generated
     */
    private String me;

    /**
     * Database Column Remarks:
     *   被关注者
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column music_friends_concern.other
     *
     * @mbg.generated
     */
    private String other;

    /**
     * Database Column Remarks:
     *   创建时间
     *
     * This field was generated by MyBatis Generator.
     * This field corresponds to the database column music_friends_concern.create_time
     *
     * @mbg.generated
     */
    private Date createTime;

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column music_friends_concern.me
     *
     * @return the value of music_friends_concern.me
     *
     * @mbg.generated
     */
    public String getMe() {
        return me;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column music_friends_concern.me
     *
     * @param me the value for music_friends_concern.me
     *
     * @mbg.generated
     */
    public void setMe(String me) {
        this.me = me == null ? null : me.trim();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column music_friends_concern.other
     *
     * @return the value of music_friends_concern.other
     *
     * @mbg.generated
     */
    public String getOther() {
        return other;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column music_friends_concern.other
     *
     * @param other the value for music_friends_concern.other
     *
     * @mbg.generated
     */
    public void setOther(String other) {
        this.other = other == null ? null : other.trim();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method returns the value of the database column music_friends_concern.create_time
     *
     * @return the value of music_friends_concern.create_time
     *
     * @mbg.generated
     */
    public Date getCreateTime() {
        return createTime;
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method sets the value of the database column music_friends_concern.create_time
     *
     * @param createTime the value for music_friends_concern.create_time
     *
     * @mbg.generated
     */
    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }
}