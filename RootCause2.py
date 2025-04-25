@Test
void testGetAllADUsers_successful() throws ApplicationException {
    String searchFilter = "(memberOf=CN=TestGroup,OU=Users,DC=example,DC=com)";
    int pageSize = 2;

    LDAPUserInfoDto mockUser1 = new LDAPUserInfoDto();
    mockUser1.setUserId("user1");

    List<LDAPUserInfoDto> pageResult = List.of(mockUser1);

    when(ldapTemplate.getContextSource()).thenReturn(contextSource);
    when(contextSource.getReadOnlyContext()).thenReturn(mock(LdapContext.class));

    // Mock LdapOperations
    LdapOperations ldapOperationsMock = mock(LdapOperations.class);
    // Capture the actual processor to control hasMore()
    PagedResultsDirContextProcessor processorMock = mock(PagedResultsDirContextProcessor.class);

    // First iteration: hasMore = true → process page
    // Second iteration: hasMore = false → exit loop
    when(processorMock.hasMore()).thenReturn(true, false);

    when(ldapOperationsMock.search(
            eq(LdapUtils.emptyLdapName()),
            eq(searchFilter),
            any(SearchControls.class),
            any(PersonAttributesMapper.class),
            eq(processorMock))
    ).thenReturn(pageResult);

    // Mock static call to SingleContextSource.doWithSingleContext
    try (MockedStatic<SingleContextSource> contextSourceMock = mockStatic(SingleContextSource.class)) {
        contextSourceMock.when(() -> SingleContextSource.doWithSingleContext(any(), any()))
                .thenAnswer(invocation -> {
                    ContextExecutor<LdapContext> executor = invocation.getArgument(1);
                    return executor.executeWithContext(ldapOperationsMock);  // <-- this executes your do-while logic
                });

        // Call the actual method
        List<LDAPUserInfoDto> result = ldapGroupsService.getAllADUsers(searchFilter, pageSize);

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("user1", result.get(0).getUserId());

        // Verify search was called once (1 loop)
        verify(ldapOperationsMock, times(1)).search(
                eq(LdapUtils.emptyLdapName()),
                eq(searchFilter),
                any(SearchControls.class),
                any(PersonAttributesMapper.class),
                eq(processorMock)
        );
    }
}
