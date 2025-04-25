@Test
void testGetAllADUsers_successful() throws ApplicationException {
    String searchFilter = "(memberOf=CN=TestGroup,OU=Users,DC=example,DC=com)";
    int pageSize = 2;

    LDAPUserInfoDto mockUser1 = new LDAPUserInfoDto();
    mockUser1.setUserId("user1");

    List<LDAPUserInfoDto> mockUserList = List.of(mockUser1);

    // Mock processor and operations
    PagedResultsDirContextProcessor processorMock = mock(PagedResultsDirContextProcessor.class);
    LdapOperations ldapOperationsMock = mock(LdapOperations.class);
    LdapContext mockContext = mock(LdapContext.class);

    // Simulate 1 iteration of do-while
    when(processorMock.hasMore()).thenReturn(true, false);
    when(ldapOperationsMock.search(
            eq(LdapUtils.emptyLdapName()),
            eq(searchFilter),
            any(SearchControls.class),
            any(PersonAttributesMapper.class),
            eq(processorMock)
    )).thenReturn(mockUserList);

    when(ldapTemplate.getContextSource()).thenReturn(contextSource);
    when(contextSource.getReadOnlyContext()).thenReturn(mockContext);

    try (MockedStatic<SingleContextSource> contextSourceMock = mockStatic(SingleContextSource.class)) {
        contextSourceMock.when(() -> SingleContextSource.doWithSingleContext(any(), any()))
                .thenAnswer(invocation -> {
                    // Extract lambda and run it to simulate real execution
                    org.springframework.ldap.core.ContextExecutor<LdapContext> executor = invocation.getArgument(1);
                    return executor.executeWithContext(ldapOperationsMock);
                });

        List<LDAPUserInfoDto> result = ldapGroupsService.getAllADUsers(searchFilter, pageSize);

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("user1", result.get(0).getUserId());
    }
}
