@Test
void testSimoLienTypesJsonConversion_throwsException() throws JsonProcessingException {
    // Arrange
    ObjectMapper mockObjectMapper = Mockito.mock(ObjectMapper.class);
    List<String> simorLienTypes = Arrays.asList("Type1", "Type2");

    // Simulate exception
    Mockito.when(mockObjectMapper.writeValueAsString(simorLienTypes))
           .thenThrow(new JsonProcessingException("Mock JSON error") {});

    // Use a spy or mock to override the Mapper.INSTANCE.getObjectMapper() call
    // This requires some trick depending on how Mapper.INSTANCE is designed

    // For illustration, let's assume Mapper.INSTANCE is a singleton and replaceable
    Mapper mockMapper = Mockito.mock(Mapper.class);
    Mockito.when(mockMapper.getObjectMapper()).thenReturn(mockObjectMapper);

    // Use a setter or reflection to inject mockMapper into your service (if possible)
    // For example:
    MyService service = new MyService();
    service.setMapper(mockMapper); // Or use reflection if no setter

    // Act
    service.yourMethodUnderTest(); // The method containing the try-catch block

    // Assert (you can verify logs or state changes if needed)
    // For example, check that simoLienType was not set or logged appropriately
}
