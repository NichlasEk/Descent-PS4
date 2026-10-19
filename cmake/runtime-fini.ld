/* The SDK script omits the finalizer table. Keep real, nonzero bounds. */
SECTIONS {
    .fini_array : ALIGN(8) {
        PROVIDE_HIDDEN(__fini_array_start = .);
        KEEP(*(SORT_BY_INIT_PRIORITY(.fini_array.*)))
        KEEP(*(.fini_array))
        PROVIDE_HIDDEN(__fini_array_end = .);
    }
}
INSERT AFTER .init_array;
