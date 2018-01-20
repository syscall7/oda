set(SOURCES
    main.cpp
)

add_library(pysnowman SHARED ${SOURCES})
target_link_libraries(pysnowman nc ${Boost_LIBRARIES} ${QT_LIBRARIES})

install(TARGETS pysnowman
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

# vim:set et sts=4 sw=4 nospell:
