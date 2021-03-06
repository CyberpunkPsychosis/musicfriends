package com.music.friends.app.dao;

import com.music.friends.app.pojo.UserInfo;

public interface UserInfoMapper {
    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_user_info
     *
     * @mbg.generated
     */
    int deleteByPrimaryKey(String id);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_user_info
     *
     * @mbg.generated
     */
    int insert(UserInfo record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_user_info
     *
     * @mbg.generated
     */
    int insertSelective(UserInfo record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_user_info
     *
     * @mbg.generated
     */
    UserInfo selectByPrimaryKey(String id);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_user_info
     *
     * @mbg.generated
     */
    int updateByPrimaryKeySelective(UserInfo record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table music_friends_user_info
     *
     * @mbg.generated
     */
    int updateByPrimaryKey(UserInfo record);

    /**
     * 根据用户Id查询用户信息
     * @param userId 用户Id
     * @return UserInfo
     */
    UserInfo selectByUserId(String userId);
}