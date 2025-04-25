@Test
void testGetAllADUsers_successful() throws ApplicationException {
    String searchFilter = "(memberOf=CN=TestGroup,OU=Users,DC=example,DC=com)";
    int pageSize = 2;

    LDAPUserInfoDto mockUser1 = new LDAPUserInfoDto();
    mockUser1.setEmpId("user1");

    List<LDAPUserInfoDto> mockUserList = List.of(mockUser1);

    // Mock the behavior of the LdapTemplate and contextSource
    when(ldapTemplate.getContextSource()).thenReturn(contextSource);
    when(contextSource.getReadOnlyContext()).thenReturn(mock(LdapContext.class));

    // Mock the behavior of SingleContextSource's static method
    try (MockedStatic<SingleContextSource> contextSourceMock = mockStatic(SingleContextSource.class)) {
        // Define the behavior of the static method `doWithSingleContext`
        contextSourceMock.when(() -> 
            SingleContextSource.doWithSingleContext(any(), any())
        ).thenAnswer(invocation -> {
            // Extract the passed lambda and invoke it manually with a mocked LdapContext
            @SuppressWarnings("unchecked")
            org.springframework.ldap.core.ContextExecutor<LdapContext> executor = 
                (org.springframework.ldap.core.ContextExecutor<LdapContext>) invocation.getArgument(1);
            // Simulate calling the lambda passed to doWithSingleContext
            return executor.executeWithContext(mock(LdapContext.class));
        });

        // Simulate calling the search method inside the do-while loop
        LdapOperations ldapOperations = mock(LdapOperations.class);
        PagedResultsDirContextProcessor processor = mock(PagedResultsDirContextProcessor.class);
        when(processor.hasMore()).thenReturn(true).thenReturn(false);  // Simulate paging behavior

        when(ldapOperations.search(
                eq(LdapUtils.emptyLdapName()), 
                eq(searchFilter), 
                any(SearchControls.class), 
                any(PersonAttributesMapper.class), 
                eq(processor)
        )).thenReturn(mockUserList);

        // Execute the service method
        List<LDAPUserInfoDto> result = ldapGroupsService.getAllADUsers(searchFilter, pageSize);

        // Assertions
        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("user1", result.get(0).getEmpId());
    }
}
